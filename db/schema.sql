BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================================================
-- 1. 사용자 (SFR-001)
-- =========================================================
CREATE TABLE app_user (
    user_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       VARCHAR(50) NOT NULL,
    password_hash  TEXT NOT NULL,
    name           VARCHAR(100) NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_app_user_username UNIQUE (username)
);

COMMENT ON TABLE app_user IS '사용자';
COMMENT ON COLUMN app_user.username IS '로그인 아이디';
COMMENT ON COLUMN app_user.password_hash IS 'pgcrypto bcrypt 해시';


-- =========================================================
-- 2. 온보딩 기초정보 (SFR-002)
-- =========================================================
CREATE TABLE onboard_profile (
    user_id          BIGINT PRIMARY KEY,
    age              INTEGER,
    menarche_age     INTEGER,
    cycle_length     INTEGER,
    cycle_regular    BOOLEAN,
    pain_history     TEXT,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_onboard_profile_user
        FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE
);

COMMENT ON TABLE onboard_profile IS '온보딩 기초정보';


-- =========================================================
-- 3. 월경 기록 (SFR-003)
-- =========================================================
CREATE TABLE period_record (
    record_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_period_record_user
        FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,

    CONSTRAINT chk_period_record_dates
        CHECK (end_date IS NULL OR end_date >= start_date)
);

COMMENT ON TABLE period_record IS '월경 기록';


-- =========================================================
-- 4. 증상/생활/호르몬 자가보고 (SFR-004~006)
-- =========================================================
CREATE TABLE diary_entry (
    diary_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        BIGINT NOT NULL,
    entry_date     DATE NOT NULL,
    headache       SMALLINT,
    stomachache    SMALLINT,
    mood           VARCHAR(20),
    mood_swing     SMALLINT,
    fatigue        SMALLINT,
    sleep_quality  SMALLINT,
    stress         SMALLINT,
    appetite       SMALLINT,
    exercise_level SMALLINT,
    sore_breasts   SMALLINT,
    food_cravings  SMALLINT,
    indigestion    SMALLINT,
    bloating       SMALLINT,
    lh             NUMERIC(8, 2),
    e3g            NUMERIC(8, 2),
    pdg            NUMERIC(8, 2),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_diary_entry_user
        FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,

    CONSTRAINT uq_diary_entry_user_date UNIQUE (user_id, entry_date)
);

COMMENT ON TABLE diary_entry IS '증상/생활/호르몬 자가보고';
COMMENT ON COLUMN diary_entry.mood_swing IS '기분 변화 정도 0~5 (data.csv moodswing_ord)';
COMMENT ON COLUMN diary_entry.appetite IS '식욕 변화 0~5 (data.csv appetite_ord)';
COMMENT ON COLUMN diary_entry.exercise_level IS '운동량 0~5 (data.csv exerciselevel_ord)';
COMMENT ON COLUMN diary_entry.sore_breasts IS '유방 압통 0~5 (data.csv sorebreasts_ord)';
COMMENT ON COLUMN diary_entry.food_cravings IS '음식 갈망 0~5 (data.csv foodcravings_ord)';
COMMENT ON COLUMN diary_entry.indigestion IS '소화불량 0~5 (data.csv indigestion_ord)';
COMMENT ON COLUMN diary_entry.bloating IS '복부 팽만 0~5 (data.csv bloating_ord)';


-- =========================================================
-- 5. 예측 결과 (SFR-007~010)
-- =========================================================
CREATE TABLE prediction_result (
    prediction_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id           BIGINT NOT NULL,
    phase             VARCHAR(20) NOT NULL,
    days_to_period    INTEGER,
    headache_risk     VARCHAR(20) NOT NULL,
    stomachache_risk  VARCHAR(20) NOT NULL,
    confidence        NUMERIC(4, 3),
    factors           JSONB,
    predicted_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_result_user
        FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE
);

COMMENT ON TABLE prediction_result IS '예측 결과 (SFR-008~010)';
COMMENT ON COLUMN prediction_result.factors IS '기여 요인 [{label, value}] JSON';


-- =========================================================
-- 6. 실제 결과 피드백 (SFR-012)
-- =========================================================
CREATE TABLE feedback_result (
    feedback_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prediction_id      BIGINT,
    user_id            BIGINT NOT NULL,
    headache_actual    BOOLEAN,
    stomachache_actual BOOLEAN,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_feedback_result_prediction
        FOREIGN KEY (prediction_id) REFERENCES prediction_result (prediction_id) ON DELETE SET NULL,

    CONSTRAINT fk_feedback_result_user
        FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE
);

COMMENT ON TABLE feedback_result IS '실제 결과 피드백';


-- =========================================================
-- 7. 모드/동의 설정 (SFR-014~015)
-- =========================================================
CREATE TABLE user_setting (
    user_id      BIGINT PRIMARY KEY,
    mode         VARCHAR(20) NOT NULL DEFAULT 'simple',
    consent      BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_setting_user
        FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,

    CONSTRAINT chk_user_setting_mode
        CHECK (mode IN ('simple', 'precision'))
);

COMMENT ON TABLE user_setting IS '예측 모드 / 동의 설정';


-- =========================================================
-- 인덱스
-- =========================================================
CREATE INDEX idx_period_record_user_id ON period_record (user_id);
CREATE INDEX idx_diary_entry_user_id ON diary_entry (user_id);
CREATE INDEX idx_prediction_result_user_id ON prediction_result (user_id);
CREATE INDEX idx_feedback_result_user_id ON feedback_result (user_id);

COMMIT;
