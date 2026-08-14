import { type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes, forwardRef } from "react";

interface FieldWrapperProps {
  label?: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
  htmlFor?: string;
}

export function FieldWrapper({ label, error, hint, children, htmlFor }: FieldWrapperProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={htmlFor} className="text-sm font-medium text-ink-700">
          {label}
        </label>
      )}
      {children}
      {hint && !error && <span className="text-xs text-ink-500">{hint}</span>}
      {error && <span className="text-xs text-severity-severe">{error}</span>}
    </div>
  );
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, id, className = "", ...rest }, ref) => {
    return (
      <FieldWrapper label={label} error={error} hint={hint} htmlFor={id}>
        <input
          ref={ref}
          id={id}
          className={`rounded-md border px-3 py-2 text-sm text-ink-900 placeholder:text-ink-300 focus:border-clinical-500 ${
            error ? "border-severity-severe" : "border-ink-100"
          } ${className}`}
          {...rest}
        />
      </FieldWrapper>
    );
  }
);
Input.displayName = "Input";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, hint, id, className = "", ...rest }, ref) => {
    return (
      <FieldWrapper label={label} error={error} hint={hint} htmlFor={id}>
        <textarea
          ref={ref}
          id={id}
          className={`rounded-md border px-3 py-2 text-sm text-ink-900 placeholder:text-ink-300 focus:border-clinical-500 ${
            error ? "border-severity-severe" : "border-ink-100"
          } ${className}`}
          {...rest}
        />
      </FieldWrapper>
    );
  }
);
Textarea.displayName = "Textarea";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  children: React.ReactNode;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, id, className = "", children, ...rest }, ref) => {
    return (
      <FieldWrapper label={label} error={error} htmlFor={id}>
        <select
          ref={ref}
          id={id}
          className={`rounded-md border bg-white px-3 py-2 text-sm text-ink-900 focus:border-clinical-500 ${
            error ? "border-severity-severe" : "border-ink-100"
          } ${className}`}
          {...rest}
        >
          {children}
        </select>
      </FieldWrapper>
    );
  }
);
Select.displayName = "Select";
