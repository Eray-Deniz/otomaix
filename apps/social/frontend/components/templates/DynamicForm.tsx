'use client'

import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import type { Template, TemplateFormField } from '@/lib/templates.types'
import { cn } from '@/lib/utils'

interface DynamicFormProps {
  template: Template
  values: Record<string, unknown>
  onChange: (fieldId: string, value: unknown) => void
}

export function DynamicForm({ template, values, onChange }: DynamicFormProps) {
  // Group fields by .group (keep order of first occurrence)
  const groups: { name: string | undefined; fields: TemplateFormField[] }[] = []
  for (const field of template.formFields) {
    const existing = groups.find((g) => g.name === field.group)
    if (existing) existing.fields.push(field)
    else groups.push({ name: field.group, fields: [field] })
  }

  return (
    <div className="space-y-5">
      {template.defaults.disclaimer && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl">
          <p className="text-xs font-semibold text-amber-800 mb-1">⚠ Otomatik Disclaimer</p>
          <p className="text-xs text-amber-700 leading-relaxed">
            {template.defaults.disclaimer}
          </p>
          <p className="text-[11px] text-amber-600 mt-2">
            Bu metin caption sonuna otomatik olarak eklenecek.
          </p>
        </div>
      )}

      {groups.map((group, gi) => (
        <div key={gi} className="space-y-3">
          {group.name && (
            <h3 className="text-xs font-bold uppercase tracking-wide text-gray-500">
              {group.name}
            </h3>
          )}
          {group.fields.map((field) => (
            <FormField
              key={field.id}
              field={field}
              value={values[field.id]}
              onChange={(v) => onChange(field.id, v)}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

function FormField({
  field,
  value,
  onChange,
}: {
  field: TemplateFormField
  value: unknown
  onChange: (v: unknown) => void
}) {
  const stringValue = value == null ? '' : String(value)

  return (
    <div className="space-y-1.5">
      <Label className="text-sm text-gray-700">
        {field.label}
        {field.required && <span className="text-red-500 ml-0.5">*</span>}
        {!field.required && (
          <span className="font-normal text-gray-400"> (opsiyonel)</span>
        )}
      </Label>

      {field.type === 'textarea' && (
        <Textarea
          value={stringValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          rows={3}
          className="resize-none text-sm"
          maxLength={field.validation?.maxLength}
        />
      )}

      {field.type === 'text' && (
        <input
          type="text"
          value={stringValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          className="w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
          maxLength={field.validation?.maxLength}
        />
      )}

      {field.type === 'url' && (
        <input
          type="url"
          value={stringValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder || 'https://...'}
          className="w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
        />
      )}

      {field.type === 'number' && (
        <div className="relative">
          <input
            type="number"
            value={stringValue}
            onChange={(e) =>
              onChange(e.target.value === '' ? '' : Number(e.target.value))
            }
            placeholder={field.placeholder}
            min={field.validation?.min}
            max={field.validation?.max}
            className={cn(
              'w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400',
              field.suffix && 'pr-8'
            )}
          />
          {field.suffix && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
              {field.suffix}
            </span>
          )}
        </div>
      )}

      {field.type === 'select' && (
        <select
          value={stringValue}
          onChange={(e) => onChange(e.target.value)}
          className="w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 bg-white"
        >
          <option value="">Seçin...</option>
          {field.options?.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )}

      {field.type === 'multi-select' && (
        <div className="flex flex-wrap gap-1.5">
          {field.options?.map((opt) => {
            const arr = Array.isArray(value) ? (value as string[]) : []
            const isSelected = arr.includes(opt.value)
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() =>
                  onChange(
                    isSelected
                      ? arr.filter((v) => v !== opt.value)
                      : [...arr, opt.value]
                  )
                }
                className={cn(
                  'px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-200 text-gray-600 hover:border-blue-300'
                )}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      )}

      {field.helpText && (
        <p className="text-xs text-gray-400">{field.helpText}</p>
      )}
    </div>
  )
}
