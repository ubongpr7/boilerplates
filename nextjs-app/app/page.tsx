import { ThemeSwitchButton } from "@/redux/theme-switch-button";

const platformName = process.env.NEXT_PUBLIC_PLATFORM_NAME || "Project Boilerplate";

export default function HomePage() {
  return (
    <main className="container">
      <section className="card">
        <div className="card-header">
          <p className="eyebrow">Next.js Boilerplate</p>
          <ThemeSwitchButton />
        </div>
        <h1>{platformName}</h1>
        <p>
          This starter is clean and ready for customization. Update
          <code> NEXT_PUBLIC_PLATFORM_NAME</code> to brand this app.
        </p>
      </section>
    </main>
  );
}
