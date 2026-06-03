export function generateAvatarUrl(firstName, lastName, email) {
  const initials = `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase().slice(0, 2)
  const fullName = `${firstName || ''} ${lastName || ''}`.trim()
  
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials || fullName || email)}&background=random&color=fff&size=128`
}
