BEGIN;

-- username1~10 / passwords 11,22,33,...,99,10, names user1~10
INSERT INTO app_user (username, password_hash, name)
SELECT
    'username' || n,
    crypt(CASE WHEN n = 10 THEN '10' ELSE (n::text || n::text) END, gen_salt('bf')),
    'user' || n
FROM generate_series(1, 10) AS n;

-- Onboarding basic info (varies slightly per person)
INSERT INTO onboard_profile (user_id, age, menarche_age, cycle_length, cycle_regular, pain_history)
SELECT
    u.user_id,
    20 + (u.user_id % 15),
    12 + (u.user_id % 3),
    26 + (u.user_id % 5),
    (u.user_id % 3 != 0),
    CASE WHEN u.user_id % 2 = 0 THEN 'Mild period pain' ELSE 'No pain' END
FROM app_user u;

-- Period records (2 recent entries each)
INSERT INTO period_record (user_id, start_date, end_date)
SELECT u.user_id, DATE '2024-04-15' - (u.user_id * 3)::int, DATE '2024-04-20' - (u.user_id * 3)::int
FROM app_user u
UNION ALL
SELECT u.user_id, DATE '2024-03-18' - (u.user_id * 3)::int, DATE '2024-03-23' - (u.user_id * 3)::int
FROM app_user u;

-- Symptom diary + hormone self-report (1 entry each)
INSERT INTO diary_entry (
    user_id, entry_date, headache, stomachache, mood, mood_swing, fatigue, sleep_quality, stress,
    appetite, exercise_level, sore_breasts, food_cravings, indigestion, bloating, lh, e3g, pdg
)
SELECT
    u.user_id,
    DATE '2024-04-16',
    (u.user_id % 5),
    (u.user_id % 5) + 1,
    'moderate',
    (u.user_id % 6),
    (u.user_id % 4),
    (u.user_id % 5) + 1,
    (u.user_id % 6),
    ((u.user_id + 1) % 6),
    ((u.user_id + 2) % 6),
    ((u.user_id + 3) % 6),
    ((u.user_id + 4) % 6),
    (u.user_id % 4),
    ((u.user_id + 2) % 5),
    5 + (u.user_id % 10),
    40 + (u.user_id % 8) * 15,
    1 + (u.user_id % 5) * 0.8
FROM app_user u;

-- Prediction results (1 entry each)
INSERT INTO prediction_result (user_id, phase, days_to_period, headache_risk, stomachache_risk, confidence, factors)
SELECT
    u.user_id,
    'Luteal',
    3 + (u.user_id % 5),
    (ARRAY['Low', 'Moderate', 'High'])[1 + (u.user_id % 3)],
    (ARRAY['Moderate', 'High', 'Very High'])[1 + (u.user_id % 3)],
    0.6 + (u.user_id % 4) * 0.1,
    '[{"label": "Hormone change (estrogen)", "value": 0.24}, {"label": "Stress index", "value": 0.18}, {"label": "Sleep quality", "value": -0.12}]'::jsonb
FROM app_user u;

-- Mode/consent settings
INSERT INTO user_setting (user_id, mode, consent)
SELECT u.user_id, CASE WHEN u.user_id % 4 = 0 THEN 'precision' ELSE 'simple' END, TRUE
FROM app_user u;

COMMIT;
