export default function InputWithPrefix({
  id,
  name,
  type = 'text',
  prefix,
  placeholder,
  value,
  onChange,
  required = false,
  className = '',
  ...props
}) {
  return (
    <div className="mt-2">
      <div className="flex items-center rounded-md bg-white/5 pl-3 outline-1 -outline-offset-1 outline-white/10 focus-within:outline-2 focus-within:-outline-offset-2 focus-within:outline-indigo-500">
        {prefix && (
          <div className="shrink-0 text-base text-gray-400 select-none sm:text-sm/6">{prefix}</div>
        )}
        <input
          id={id}
          name={name}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          required={required}
          className={`block min-w-0 grow bg-transparent py-1.5 pr-3 pl-1 text-base text-white placeholder:text-gray-500 focus:outline-none sm:text-sm/6 ${className}`}
          {...props}
        />
      </div>
    </div>
  )
}
