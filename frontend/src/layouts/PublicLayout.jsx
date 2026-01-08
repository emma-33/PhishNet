import { Outlet } from "react-router-dom";

export default function PublicLayout() {
    return (
        <main className="min-h-screen p-6">
            <Outlet />
        </main>
    )
}