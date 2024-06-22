/*
 * Data fixture for e2e testing.
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
    'User',
    'NeedsOnboarding'
);

INSERT INTO public.deposit__tenancy (
    id,
    created_at,
    deleted_at,
    deposit_in_p,
    start_date,
    end_date,
    user_id
)
VALUES(
    'b99643d3-f0ff-40b5-a0b5-c07af587f382'::uuid,
    now(),
    NULL,
    0,
    NULL,
    '2024-04-28',  -- TODO: make dynamic
    '63d3c89c-c699-4c29-944b-01e506e58fea'::uuid -- needs_onboarding@example.com
);
