class SQLQueries:
    class AccessTokens:
        get_all_tokens = 'SELECT * from public.access_tokens'
        get_token_by_id = 'SELECT * from public.access_tokens WHERE id = %s;'

    class Users:
        get_user_id_by_email = 'SELECT id from public.users WHERE email = %s;'
