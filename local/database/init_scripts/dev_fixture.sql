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
    '95e72f5e-bb75-48ca-94e0-7b485d23f0c3',
    now(),
    NULL,
    true,
    'admin@example.com',
    '$argon2id$v=19$m=65536,t=3,p=4$sVduMqKKFO6nC+Sglre5oQ$301ht+a6A4LEH8PicBmwuY1SHxdN5Wtn90qHDWGwMvk',
    true,
    true,
    now(),
    NULL,
    NULL,
    NULL
),
(
    '12055aef-8e6b-41b5-8bb0-cea7f578af6a',
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
