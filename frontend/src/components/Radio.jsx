export default function Radio({
  id,
  name,
  value,
  checked,
  defaultChecked,
  onChange,
  disabled = false,
  className = '',
  ...props
}) {
  return (
    <input
      id={id}
      name={name}
      type="radio"
      value={value}
      checked={checked}
      defaultChecked={defaultChecked}
      onChange={onChange}
      disabled={disabled}
      className={`relative size-4 appearance-none rounded-full border border-white/10 bg-white/5 before:absolute before:inset-1 before:rounded-full before:bg-white not-checked:before:hidden checked:border-indigo-500 checked:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 disabled:border-white/5 disabled:bg-white/10 disabled:before:bg-white/20 forced-colors:appearance-auto forced-colors:before:hidden ${className}`}
      {...props}
    />
  )
}
