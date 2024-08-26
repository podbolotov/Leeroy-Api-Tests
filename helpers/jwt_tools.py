import jwt
from data.framework_variables import FrameworkVariables as FrVars
from models.jwt import DecodedJsonWebToken


def validate_and_decode_token(token: str) -> DecodedJsonWebToken:
    decoded_token = jwt.decode(token, FrVars.JWT_SIGNATURE_SECRET, algorithms="HS256")
    return DecodedJsonWebToken(
        id=decoded_token['id'],
        user_id=decoded_token['user_id'],
        issued_at=decoded_token['issued_at'],
        expired_at=decoded_token['expired_at']
    )
