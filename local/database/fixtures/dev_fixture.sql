/*
 * Data fixture for local development.
 * All user passwords are 'password'.
 *
 * (c) 2024 Alberto Morón Hernández
 */

INSERT INTO public.auth__user (
    id,
    created_at,
    deleted_at,
    is_superuser,
    email,
    hashed_password,
    is_active,
    is_verified,
    verified_at,
    completed_onboarding_at,
    first_name,
    family_name
)
VALUES (
    '95e72f5e-bb75-48ca-94e0-7b485d23f0c3'::uuid,
    now(),
    NULL,
    true,
    'admin@example.com',
    '$argon2id$v=19$m=65536,t=3,p=4$sVduMqKKFO6nC+Sglre5oQ$301ht+a6A4LEH8PicBmwuY1SHxdN5Wtn90qHDWGwMvk',
    true,
    true,
    now(),
    now(),
    'User',
    'Admin'
), (
    '8c9356f7-3fb3-486a-8481-346b7ffe62f0'::uuid,
    now(),
    NULL,
    false,
    'active_verified@example.com',
    '$argon2id$v=19$m=65536,t=3,p=4$sVduMqKKFO6nC+Sglre5oQ$301ht+a6A4LEH8PicBmwuY1SHxdN5Wtn90qHDWGwMvk',
    true,
    true,
    now(),
    now(),
    'User',
    'ActiveVerified'
), (
    '63d3c89c-c699-4c29-944b-01e506e58fea'::uuid,
    now(),
    NULL,
    false,
    'needs_onboarding@example.com',
    '$argon2id$v=19$m=65536,t=3,p=4$sVduMqKKFO6nC+Sglre5oQ$301ht+a6A4LEH8PicBmwuY1SHxdN5Wtn90qHDWGwMvk',
    true,
    true,
    now(),
    NULL,
    'UserName',
    'NeedsOnboarding'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.deposit__tenancy (
    id,
    created_at,
    deleted_at,
    deposit_in_p,
    start_date,
    end_date,
    user_id
)
VALUES (
    '75039111-95fc-4cf9-908b-48859896b9cc'::uuid,
    now(),
    NULL,
    92400,
    '2020-01-12',
    '2024-06-25',
    '8c9356f7-3fb3-486a-8481-346b7ffe62f0'::uuid -- active_verified@example.com
), (
    'b99643d3-f0ff-40b5-a0b5-c07af587f382'::uuid,
    now(),
    NULL,
    0,
    NULL,
    CURRENT_DATE - INTERVAL '5 days',
    '63d3c89c-c699-4c29-944b-01e506e58fea'::uuid -- needs_onboarding@example.com
)
ON CONFLICT (id) DO NOTHING;
