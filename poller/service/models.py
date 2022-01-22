#!/usr/bin/env python3


from pydantic import BaseModel, EmailStr
from pydantic import validator
import validators


# Validator methods
def valid_url_path(param: str) -> str:
    if not param.islower():
        raise ValueError("name must be valid URL path, must be lowercase")
    if not validators.url(f'http://localhost/{param}'):
        raise ValueError("name must be a valid URL path, URL path invalid")
    return param


# Service schema models
class Version(BaseModel):
    version: str


class ProjectCore(BaseModel):
    name: str
    title: str


class Project(ProjectCore):
    description: str


class ProjectInput(Project):
    # Needs to be valid path in URL (for now, basic checks)
    _name_is_valid_url = validator('name', allow_reuse=True)(valid_url_path)

    class Config:
        schema_extra = {
            "example": {
                "name": "vxlan-evpn-core",
                "title": "VXLAN EVPN Multisite Core Technologies",
                "description": "An environment to demonstrate foundational VXLAN EVPN Multisite Core technologies." # noqa
            }
        }


class ScenarioCore(BaseModel):
    name: str
    title: str
    project: str


class Scenario(ScenarioCore):
    description: str


class ScenarioInput(Scenario):
    # Scenario name needs to be valid path in URL
    _scenario_is_valid_url = validator('name', allow_reuse=True)(valid_url_path)

    # Project name needs to be valid path in URL (valid project validated later)
    _project_is_valid_url = validator('project', allow_reuse=True)(valid_url_path)

    class Config:
        schema_extra = {
            "example": {
                "name": "vpc-bgw-as-dci",
                "title": "VXLAN EVPN Multisite Core Technologies",
                "description": "An environment to demonstrate foundational VXLAN EVPN Multisite Core technologies.", # noqa
                "project": "vxlan-evpn-core"
            }
        }


class LeaseRequest(BaseModel):
    ttl: int


class Lease(LeaseRequest):
    id: int


class ReservationEmail(BaseModel):
    email: EmailStr


class ReservationProject(BaseModel):
    project: str


class ReservationCore(ReservationEmail, ReservationProject):
    pass


class Reservation(ReservationCore, Lease):
    pass


class ReservationInput(ReservationCore):
    # Email validation is "for free" with EmailStr

    # Project name needs to be valid path in URL (valid project validated later)
    _project_is_valid_url = validator('project', allow_reuse=True)(valid_url_path)

    duration: int
