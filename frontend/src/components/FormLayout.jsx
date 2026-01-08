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
    <div className={borderBottom ? 'border-b border-white/10 pb-12' : ''}>
      <h2 className="text-base/7 font-semibold text-white">{title}</h2>
      {description && (
        <p className="mt-1 text-sm/6 text-gray-400">{description}</p>
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
      <label htmlFor={id} className="block text-sm/6 font-medium text-white">
        {label}
        {required && <span className="text-red-400 ml-1">*</span>}
      </label>
      {children}
      {description && (
        <p className="mt-3 text-sm/6 text-gray-400">{description}</p>
      )}
    </div>
  )
}

export function FormActions({ onCancel, cancelLabel = 'Cancel', submitLabel = 'Save' }) {
  return (
    <div className="mt-6 flex items-center justify-end gap-x-6">
      {onCancel && (
        <button type="button" onClick={onCancel} className="text-sm/6 font-semibold text-white hover:text-gray-300">
          {cancelLabel}
        </button>
      )}
      <button
        type="submit"
        className="rounded-md bg-indigo-500 px-3 py-2 text-sm font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 hover:bg-indigo-400"
      >
        {submitLabel}
      </button>
    </div>
  )
}
