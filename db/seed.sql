BEGIN;

-- 아이디1~10 / 비밀번호는 11,22,33,...,99,10, 이름은 사용자1~10
INSERT INTO app_user (username, password_hash, name)
SELECT
    '아이디' || n,
    crypt(CASE WHEN n = 10 THEN '10' ELSE (n::text || n::text) END, gen_salt('bf')),
    '사용자' || n
FROM generate_series(1, 10) AS n;

-- 온보딩 기초정보 (사람마다 조금씩 다르게)
INSERT INTO onboard_profile (user_id, age, menarche_age, cycle_length, cycle_regular, pain_history)
SELECT
    u.user_id,
    20 + (u.user_id % 15),
    12 + (u.user_id % 3),
    26 + (u.user_id % 5),
    (u.user_id % 3 != 0),
    CASE WHEN u.user_id % 2 = 0 THEN '경미한 생리통 있음' ELSE '통증 없음' END
FROM app_user u;

-- 월경 기록 (최근 2건씩)
INSERT INTO period_record (user_id, start_date, end_date)
SELECT u.user_id, DATE '2024-04-15' - (u.user_id * 3)::int, DATE '2024-04-20' - (u.user_id * 3)::int
FROM app_user u
UNION ALL
SELECT u.user_id, DATE '2024-03-18' - (u.user_id * 3)::int, DATE '2024-03-23' - (u.user_id * 3)::int
FROM app_user u;

-- 증상 다이어리 + 호르몬 자가보고 (1건씩)
INSERT INTO diary_entry (user_id, entry_date, headache, stomachache, mood, fatigue, sleep_quality, stress, lh, e3g, pdg)
SELECT
    u.user_id,
    DATE '2024-04-16',
    (u.user_id % 5),
    (u.user_id % 5) + 1,
    '보통',
    (u.user_id % 4),
    (u.user_id % 5) + 1,
    (u.user_id % 6),
    5 + (u.user_id % 10),
    40 + (u.user_id % 8) * 15,
    1 + (u.user_id % 5) * 0.8
FROM app_user u;

-- 예측 결과 (1건씩)
INSERT INTO prediction_result (user_id, phase, days_to_period, headache_risk, stomachache_risk, confidence, factors)
SELECT
    u.user_id,
    'luteal',
    3 + (u.user_id % 5),
    (ARRAY['낮음', '보통', '높음'])[1 + (u.user_id % 3)],
    (ARRAY['보통', '높음', '매우높음'])[1 + (u.user_id % 3)],
    0.6 + (u.user_id % 4) * 0.1,
    '[{"label": "호르몬 변화 (에스트로겐)", "value": 0.24}, {"label": "스트레스 지수", "value": 0.18}, {"label": "수면 품질", "value": -0.12}]'::jsonb
FROM app_user u;

-- 모드/동의 설정
INSERT INTO user_setting (user_id, mode, consent)
SELECT u.user_id, CASE WHEN u.user_id % 4 = 0 THEN 'precision' ELSE 'simple' END, TRUE
FROM app_user u;

COMMIT;
