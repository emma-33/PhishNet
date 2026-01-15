export default function FormLayout({ children, onSubmit, actions }) {
  return (
    <form onSubmit={onSubmit}>
      <div className="space-y-12">
        {children}
      </div>
      {actions}
    </form>
  )
}

export function FormSection({ title, description, children, borderBottom = true }) {
  return (
    <div className={borderBottom ? 'border-b border-gray-200 pb-12' : ''}>
      <h2 className="text-base/7 font-semibold text-gray-900">{title}</h2>
      {description && (
        <p className="mt-1 text-sm/6 text-gray-600">{description}</p>
      )}
      <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
        {children}
      </div>
    </div>
  )
}

export function FormField({ label, id, required, description, colSpan = 'col-span-full', children }) {
  const colSpanClass = colSpan === 'col-span-full' ? 'col-span-full' : colSpan
  
  return (
    <div className={colSpanClass}>
      <label htmlFor={id} className="block text-sm/6 font-medium text-gray-900">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {description && (
        <p className="mt-3 text-sm/6 text-gray-600">{description}</p>
      )}
    </div>
  )
}

export function FormActions({ onCancel, cancelLabel = 'Cancel', submitLabel = 'Save' }) {
  return (
    <div className="mt-6 flex items-center justify-end gap-x-6">
      {onCancel && (
        <button type="button" onClick={onCancel} className="text-sm/6 font-semibold text-gray-900 hover:text-gray-700">
          {cancelLabel}
        </button>
      )}
      <button
        type="submit"
        className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 hover:bg-blue-500"
      >
        {submitLabel}
      </button>
    </div>
  )
}
