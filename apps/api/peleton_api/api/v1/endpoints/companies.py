import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from peleton_api.core.database import get_db
from peleton_api.models import models
from peleton_api.schemas import company as schemas

router = APIRouter()
BRREG_API_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


@router.get("/search", response_model=schemas.CompanySearchResponse, summary="Søk etter bedrifter i Brønnøysund")
async def search_brreg_companies(
    query: str = Query(..., min_length=2, description="Søketekst for bedriftsnavn eller org.nr")
):
    params = {"navn": query, "size": 10}

    clean_query = query.replace(" ", "")
    if clean_query.isdigit() and len(clean_query) == 9:
        params = {"organisasjonsnummer": clean_query}

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(BRREG_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Kunne ikke hente data fra Brønnøysundregistrene: {e!s}"
            )

    results = []
    enheter = data.get("_embedded", {}).get("enheter", [])

    for item in enheter:
        forretningsadresse = item.get("forretningsadresse", {})
        postadresse = item.get("postadresse", {})
        postal_code = forretningsadresse.get("postnummer") or postadresse.get("postnummer")

        naeringskode = item.get("naeringskode1", {})
        category_desc = naeringskode.get("beskrivelse") if naeringskode else None

        results.append(
            schemas.CompanySearchItem(
                org_number=item.get("organisasjonsnummer"),
                name=item.get("navn"),
                postal_code=postal_code,
                company_type=item.get("organisasjonsform", {}).get("kode"),
                company_category=category_desc
            )
        )

    return schemas.CompanySearchResponse(results=results)


@router.get("", response_model=list[schemas.CompanyResponse], summary="List alle registrerte bedrifter")
def list_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).all()


@router.post("", response_model=schemas.CompanyResponse, status_code=status.HTTP_201_CREATED, summary="Opprett ny bedrift")
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Company).filter(models.Company.org_number == company.org_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organisasjonsnummer er allerede registrert"
        )

    db_company = models.Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company