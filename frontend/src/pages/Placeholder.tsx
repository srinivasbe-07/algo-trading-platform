export function Placeholder({ title, description }: { title: string; description: string }) {
  return (
    <div>
      <h1>{title}</h1>
      <p className="sub">{description}</p>
      <div className="panel">
        <p>This screen is designed and coming soon — see the mockup in docs/ux.</p>
      </div>
    </div>
  );
}
