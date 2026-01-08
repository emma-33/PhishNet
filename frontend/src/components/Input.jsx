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
        className={`block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6 ${className}`}
        {...props}
      />
    </div>
  )
}
