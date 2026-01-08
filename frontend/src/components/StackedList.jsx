import { generateAvatarUrl } from '../utils/avatarUtils'

export default function StackedList({ items = [] }) {

  const getDisplayName = (item) => {
    if (item.name) return item.name
    const fullName = `${item.first_name || ''} ${item.last_name || ''}`.trim()
    return fullName || item.email
  }

  const getRole = (item) => {
    if (item.role) return item.role
    if (item.is_operator) return 'Operator'
    return item.is_admin ? 'Admin' : 'User'
  }

  const getImageUrl = (item) => {
    if (item.imageUrl) return item.imageUrl
    return generateAvatarUrl(item.first_name, item.last_name, item.email)
  }

  return (
    <ul role="list" className="divide-y divide-white/5">
      {items.map((item) => (
        <li key={item.email || item.id} className="flex justify-between gap-x-6 py-5">
          <div className="flex min-w-0 gap-x-4">
            <img
              alt=""
              src={getImageUrl(item)}
              className="size-12 flex-none rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10"
            />
            <div className="min-w-0 flex-auto">
              <p className="text-sm/6 font-semibold text-white">{getDisplayName(item)}</p>
              <p className="mt-1 truncate text-xs/5 text-gray-400">{item.email}</p>
            </div>
          </div>
          <div className="hidden shrink-0 sm:flex sm:flex-col sm:items-end">
            <p className="text-sm/6 text-white">{getRole(item)}</p>
          </div>
        </li>
      ))}
    </ul>
  )
}
