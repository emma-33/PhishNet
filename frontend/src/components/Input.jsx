export default function Input({
  id,
  name,
  type = 'text',
  required = false,
  autoComplete,
  placeholder,
  value,
  onChange,
  className = '',
  ...props
}) {
  return (
    <div className="mt-2">
      <input
        id={id}
        name={name}
        type={type}
        required={required}
        autoComplete={autoComplete}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`block w-full rounded-md border border-gray-300 bg-white px-3 py-1.5 text-base text-gray-900 placeholder:text-gray-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm/6 ${className}`}
        {...props}
      />
    </div>
  )
}
