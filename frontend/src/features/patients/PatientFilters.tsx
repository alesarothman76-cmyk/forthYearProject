import { Search } from "lucide-react";
import { Select } from "../../components/Input";
import { SEVERITY_LABELS } from "../../lib/formatters";
import type { DiseaseSeverity, Gender } from "../../api/types";
import type { PatientListParams } from "../../api/endpoints/patients";

const SEVERITY_VALUES: DiseaseSeverity[] = [
  "NonDemented",
  "VeryMildDemented",
  "MildDemented",
  "ModerateDemented",
];

export function PatientFilters({
  filters,
  onChange,
}: {
  filters: PatientListParams;
  onChange: (next: PatientListParams) => void;
}) {
  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="relative flex-1 min-w-[200px]">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-300" />
        <input
          value={filters.search ?? ""}
          onChange={(event) => onChange({ ...filters, search: event.target.value })}
          placeholder="Search by name or national ID"
          className="w-full rounded-md border border-ink-100 py-2 pl-9 pr-3 text-sm focus:border-clinical-500"
        />
      </div>
      <Select
        aria-label="Filter by gender"
        value={filters.gender ?? ""}
        onChange={(event) =>
          onChange({ ...filters, gender: (event.target.value || undefined) as Gender | undefined })
        }
        className="w-36"
      >
        <option value="">All genders</option>
        <option value="MALE">Male</option>
        <option value="FEMALE">Female</option>
      </Select>
      <Select
        aria-label="Filter by archive status"
        value={filters.isActive ?? "true"}
        onChange={(event) =>
          onChange({ ...filters, isActive: event.target.value as PatientListParams["isActive"] })
        }
        className="w-36"
      >
        <option value="true">Active</option>
        <option value="false">Archived</option>
        <option value="all">All patients</option>
      </Select>
      <Select
        aria-label="Filter by current status"
        value={filters.status ?? ""}
        onChange={(event) =>
          onChange({ ...filters, status: (event.target.value || undefined) as DiseaseSeverity | undefined })
        }
        className="w-40"
      >
        <option value="">All statuses</option>
        {SEVERITY_VALUES.map((value) => (
          <option key={value} value={value}>
            {SEVERITY_LABELS[value]}
          </option>
        ))}
      </Select>
    </div>
  );
}
