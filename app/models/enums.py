import enum


class UserRole(str, enum.Enum):
    field_worker = "field_worker"        # case & patient entry
    district_officer = "district_officer"  # verification / status update
    lab_staff = "lab_staff"              # lab result entry
    program_manager = "program_manager"  # dashboards / read-only oversight
    admin = "admin"                      # user & system administration


class Sex(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class VaccinationStatus(str, enum.Enum):
    vaccinated = "vaccinated"
    unvaccinated = "unvaccinated"
    unknown = "unknown"


class CaseStatus(str, enum.Enum):
    suspected = "suspected"
    probable = "probable"
    confirmed = "confirmed"
    discarded = "discarded"


class LabResultValue(str, enum.Enum):
    pending = "pending"
    igm_positive = "igm_positive"
    igm_negative = "igm_negative"
    pcr_positive = "pcr_positive"
    pcr_negative = "pcr_negative"
    indeterminate = "indeterminate"


class LocationType(str, enum.Enum):
    division = "division"
    district = "district"
    upazila = "upazila"
