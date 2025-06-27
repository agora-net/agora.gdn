import { useState } from "react";

export const NewsletterForm = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const location = form.dataset.formLocation || "";

    if (!email) {
      setMessage("Please enter your email address.");
      return;
    }

    try {
      const response = await fetch("/api/v1/newsletter/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, location }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        setEmail("");
      } else {
        setMessage(data.detail || "An error occurred.");
      }
    } catch (error) {
      setMessage("An error occurred.");
    }
  };

  if (message.includes("Thank you")) {
    return <p>{message}</p>;
  }

  return (
    <form data-form="newsletter" onSubmit={handleSubmit}>
       <h6 className="footer-title">Newsletter</h6>
      <fieldset className="w-full lg:w-80">
          <label>Enter your email address</label>
          <div className="join w-full">
              <input type="email"
                     placeholder="name@example.com"
                     value={email}
                     onChange={(e) => setEmail(e.target.value)}
                     className="input input-bordered join-item" />
              <button type="submit" className="btn btn-primary join-item">Subscribe</button>
          </div>
      </fieldset>
      {message && <p className="text-error mt-2">{message}</p>}
    </form>
  );
};
