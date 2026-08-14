import { useNavigate } from "react-router-dom";
import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { useUploadScan } from "./hooks";
import { Button } from "../../components/Button";
import { ErrorBanner } from "../../components/ErrorBanner";
import type { ApiError } from "../../api/types";

export function ScanUploadForm({ patientId }: { patientId: number }) {
  const navigate = useNavigate();
  const uploadScan = useUploadScan();
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setError(null);
    setProgress(0);
    try {
      const scan = await uploadScan.mutateAsync({
        patientId,
        file,
        onProgress: setProgress,
      });
      navigate(`/scans/${scan.id}`);
    } catch (err) {
      setError((err as ApiError).detail);
    }
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => event.key === "Enter" && inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          const file = event.dataTransfer.files?.[0];
          if (file) handleFile(file);
        }}
        className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed px-6 py-10 text-center transition-colors ${
          isDragging ? "border-clinical-500 bg-clinical-100/40" : "border-ink-100 hover:border-clinical-300"
        }`}
      >
        <UploadCloud className="h-7 w-7 text-clinical-500" />
        <p className="text-sm font-medium text-ink-700">Drop an MRI scan here, or click to browse</p>
        <p className="text-xs text-ink-500">DICOM (.dcm) or standard image formats (PNG, JPEG, TIFF)</p>
        <input
          ref={inputRef}
          type="file"
          accept=".dcm,image/*"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>

      {uploadScan.isPending && (
        <div className="mt-4">
          <div className="h-2 w-full overflow-hidden rounded-full bg-ink-100">
            <div
              className="h-full bg-clinical-500 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-1 text-xs text-ink-500">
            {progress < 100 ? `Uploading… ${progress}%` : "Processing scan…"}
          </p>
        </div>
      )}

      {error && (
        <div className="mt-4">
          <ErrorBanner message={error} />
        </div>
      )}

      {!uploadScan.isPending && (
        <div className="mt-3 flex justify-end">
          <Button variant="ghost" size="sm" onClick={() => inputRef.current?.click()}>
            Choose file
          </Button>
        </div>
      )}
    </div>
  );
}
