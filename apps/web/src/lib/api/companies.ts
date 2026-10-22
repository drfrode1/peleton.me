const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CompanySearchItem {
  org_number: string;
  name: string;
  postal_code?: string;
  company_type?: string;
  company_category?: string;
}

export interface CompanySearchResponse {
  results: CompanySearchItem[];
}

export interface Company {
  id: number;
  org_number: string;
  name: string;
  postal_code?: string;
  company_type?: string;
  company_category?: string;
  show_name_consent: boolean;
}

export async function searchBrregCompanies(query: string, baseUrl = API_URL): Promise<CompanySearchItem[]> {
  if (!query || query.trim().length < 2) return [];
  const res = await fetch(`${baseUrl}/api/v1/companies/search?query=${encodeURIComponent(query.trim())}`);
  if (!res.ok) {
    throw new Error(`Failed to search companies: ${res.statusText} (${res.status})`);
  }
  const data: CompanySearchResponse = await res.json();
  return data.results || [];
}

export async function registerCompany(
  company: { org_number: string; name: string; postal_code?: string; company_type?: string; company_category?: string },
  baseUrl = API_URL
): Promise<Company> {
  const res = await fetch(`${baseUrl}/api/v1/companies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(company),
  });
  if (!res.ok) {
    throw new Error(`Failed to register company: ${res.statusText} (${res.status})`);
  }
  return res.json();
}
