"""Opt-in OIDC JWT verification with cached JWKS via PyJWT PyJWKClient."""
import os
from fastapi import Header,HTTPException
def oidc_auth(authorization:str|None=Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401,"Bearer token required")
    issuer=os.getenv("PORINI_OIDC_ISSUER")
    audience=os.getenv("PORINI_OIDC_AUDIENCE")
    jwks=os.getenv("PORINI_OIDC_JWKS_URI")
    if not all((issuer,audience,jwks)):
        raise HTTPException(503,"OIDC not configured")
    try:
        import jwt
        from jwt import PyJWKClient
        token=authorization[7:]
        key=PyJWKClient(jwks).get_signing_key_from_jwt(token).key
        claims=jwt.decode(token,key,algorithms=["RS256"],audience=audience,issuer=issuer,
                          options={"require":["exp","iat","iss","aud","sub"]},leeway=30)
        tenant=os.getenv("PORINI_TENANT_ID","demo-conservancy")
        if claims.get("tenant_id")!=tenant:raise HTTPException(403,"Wrong conservancy")
        roles=set(claims.get("roles",[]))
        return "admin" if "porini:admin" in roles else "ranger" if "porini:ranger" in roles else "sensor" if "porini:sensor" in roles else _deny()
    except HTTPException:raise
    except Exception:raise HTTPException(401,"Invalid bearer token")
def _deny():raise HTTPException(403,"Role not assigned")
