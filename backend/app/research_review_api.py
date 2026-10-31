"""Authenticated research review routes, fail-closed by default."""
import os
from fastapi import APIRouter, Depends, HTTPException, Header
from .oidc import verified_claims
from pydantic import BaseModel, Field
from .review_queue import ReviewQueue

class Candidate(BaseModel):
    evidence_id:str=Field(min_length=1,max_length=128)
    candidate:dict

class Decision(BaseModel):
    reviewer_id:str=Field(min_length=2,max_length=120)
    decision:str
    note:str=Field(default="",max_length=1000)

def bind_research_reviews(allowed_role):
    router=APIRouter(prefix="/research/reviews",tags=["research review"])
    def service():
        db=os.getenv("PORINI_REVIEW_DB")
        tenant=os.getenv("PORINI_TENANT_ID")
        if not db or not tenant:
            raise HTTPException(503,"Configure PORINI_REVIEW_DB and PORINI_TENANT_ID")
        return ReviewQueue(db),tenant
    @router.post("")
    def enqueue(req:Candidate,role=Depends(allowed_role("admin","ranger"))):
        queue,tenant=service()
        try:return queue.enqueue(tenant,req.evidence_id,req.candidate)
        except ValueError as e:raise HTTPException(422,str(e))
    @router.get("")
    def list_reviews(status:str="pending",role=Depends(allowed_role("admin","ranger"))):
        queue,tenant=service()
        try:return queue.list(tenant,status)
        except ValueError as e:raise HTTPException(422,str(e))
    @router.post("/{review_id}/decision")
    def decide(review_id:str,req:Decision,
               role=Depends(allowed_role("admin","ranger")),
               authorization:str|None=Header(default=None)):
        if os.getenv("PORINI_AUTH_MODE") != "oidc":
            raise HTTPException(403,"Decisions require OIDC authentication")
        claims=verified_claims(authorization)
        roles=set(claims.get("roles",[]))
        if not roles.intersection({"porini:admin","porini:ranger"}):
            raise HTTPException(403,"Reviewer role required")
        principal=claims.get("sub")
        if not principal or not isinstance(principal,str):
            raise HTTPException(403,"Verified reviewer subject missing")
        queue,tenant=service()
        if req.decision not in ("confirmed","rejected"):
            raise HTTPException(422,"Invalid decision")
        # Reviewer attribution comes ONLY from the validated token.
        try:return queue.decide(tenant,review_id,principal,req.decision,req.note)
        except ValueError as e:raise HTTPException(409,str(e))
    return router
