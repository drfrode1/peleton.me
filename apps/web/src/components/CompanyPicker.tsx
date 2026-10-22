import { useState, useEffect, useRef } from 'react';
import { Search, Building2, Check, X, Loader2 } from 'lucide-react';
import { searchBrregCompanies, type CompanySearchItem } from '../lib/api/companies';

interface CompanyPickerProps {
  id?: string;
  label?: string;
  selected: CompanySearchItem | null;
  onSelect: (company: CompanySearchItem | null) => void;
}

export function CompanyPicker({
  id = 'company-picker',
  label = 'Company or organization number',
  selected,
  onSelect,
}: CompanyPickerProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<CompanySearchItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Debounced search
  useEffect(() => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const handler = setTimeout(async () => {
      setIsLoading(true);
      setErrorMessage('');
      try {
        const items = await searchBrregCompanies(searchTerm);
        setResults(items);
        setIsOpen(true);
      } catch (err) {
        setErrorMessage(err instanceof Error ? err.message : 'Could not fetch organizations');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(handler);
  }, [searchTerm]);

  // Click outside to close
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative w-full" ref={dropdownRef}>
      {label && (
        <label htmlFor={id} className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          {label}
        </label>
      )}

      {selected ? (
        <div className="flex items-center justify-between p-3.5 bg-slate-900 border border-emerald-500/40 rounded-lg">
          <div className="flex items-center gap-3">
            <Building2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-white">{selected.name}</p>
              <p className="text-xs text-slate-400">Org. nr: {selected.org_number} {selected.postal_code ? `· ${selected.postal_code}` : ''}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onSelect(null)}
            className="p-1 hover:bg-slate-800 text-slate-400 hover:text-white rounded transition"
            aria-label="Remove selected company"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin text-emerald-400" /> : <Search className="w-4 h-4" />}
          </div>
          <input
            id={id}
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => results.length > 0 && setIsOpen(true)}
            placeholder="Search Brønnøysund Registry (name or 9-digit org.nr)..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900/80 border border-slate-800 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
          />
        </div>
      )}

      {isOpen && !selected && (
        <div className="absolute z-50 w-full mt-2 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl max-h-64 overflow-y-auto divide-y divide-slate-800/60">
          {results.length > 0 ? (
            results.map((item) => (
              <button
                key={item.org_number}
                type="button"
                onClick={() => {
                  onSelect(item);
                  setIsOpen(false);
                  setSearchTerm('');
                }}
                className="w-full text-left px-4 py-3 hover:bg-slate-800/80 flex items-center justify-between transition group"
              >
                <div>
                  <p className="text-sm font-medium text-slate-200 group-hover:text-emerald-400 transition">
                    {item.name}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Org. nr: {item.org_number} {item.postal_code ? `· Postnr: ${item.postal_code}` : ''}
                    {item.company_category ? ` · ${item.company_category}` : ''}
                  </p>
                </div>
                <Check className="w-4 h-4 text-emerald-400 opacity-0 group-hover:opacity-100 transition" />
              </button>
            ))
          ) : (
            <div className="p-4 text-center text-xs text-slate-500">
              {errorMessage || 'No organizations found matching your search.'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
