import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50",
        variant === "primary" && "bg-accent text-accent-foreground hover:opacity-90",
        variant === "ghost" && "text-sidebar-foreground hover:bg-white/10",
        className,
      )}
      {...props}
    />
  );
}
