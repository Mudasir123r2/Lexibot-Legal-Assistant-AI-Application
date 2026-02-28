import { useContext, useMemo, useState } from "react";
import { AuthContext } from "../../context/AuthContext";
import { Link, useNavigate } from "react-router-dom";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { FaBalanceScale } from "react-icons/fa";
import { FiMail, FiLock, FiEye, FiEyeOff } from "react-icons/fi";

const LoginSchema = Yup.object({
  email: Yup.string()
    .email("Please enter a valid email address")
    .required("Email is required"),
  password: Yup.string()
    .min(8, "Password must be at least 8 characters")
    .max(72, "Password cannot exceed 72 characters")
    .required("Password is required"),
  remember: Yup.boolean(),
});

export default function Login() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [showPass, setShowPass] = useState(false);
  const remembered = useMemo(() => localStorage.getItem("remember_email") || "", []);

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0a0a0b]">
      {/* Dark mesh gradients behind the page */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        {/* subtle vignette */}
        <div className="absolute inset-0 bg-[radial-gradient(120%_90%_at_50%_0%,rgba(255,255,255,0.06)_0%,transparent_60%),radial-gradient(90%_70%_at_0%_0%,rgba(99,102,241,0.10)_0%,transparent_60%),radial-gradient(90%_70%_at_100%_0%,rgba(236,72,153,0.10)_0%,transparent_60%)]" />
        {/* glow blobs */}
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 h-80 w-80 rounded-full bg-gradient-to-tr from-indigo-500/20 via-fuchsia-500/10 to-emerald-400/10 blur-3xl" />
        <div className="absolute -bottom-24 -right-10 h-96 w-96 rounded-full bg-gradient-to-br from-fuchsia-600/15 to-indigo-600/10 blur-3xl" />
      </div>

      <div className="w-full max-w-md px-4">
        {/* gradient ring halo */}
        <div className="relative">
          <div className="absolute -inset-[2px] rounded-3xl bg-[conic-gradient(from_140deg,rgba(99,102,241,.35),rgba(236,72,153,.35),rgba(16,185,129,.35),rgba(99,102,241,.35))] blur md:blur-md opacity-70" />
          {/* glass card with inner radial highlight */}
          <div className="relative rounded-3xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-[0_10px_40px_rgba(0,0,0,0.6)] p-8
                          bg-[radial-gradient(120%_120%_at_50%_-10%,rgba(255,255,255,0.07)_0%,transparent_55%)]">
            <div className="flex items-center justify-center gap-2 mb-2">
              <div className="h-10 w-10 rounded-xl bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10">
                <FaBalanceScale className="text-lg" />
              </div>
              <span className="text-2xl font-semibold text-slate-100">LexiBot</span>
            </div>

            <h1 className="text-xl font-bold text-center text-white">Welcome to LexiBot</h1>
            <p className="text-center text-slate-400 text-sm mb-6">
              Secure access for clients, advocates, and admins.
            </p>

            <Formik
              initialValues={{ email: remembered, password: "", remember: !!remembered }}
              validationSchema={LoginSchema}
              validateOnBlur
              validateOnChange
              onSubmit={async (values, { setStatus, setSubmitting }) => {
                setStatus(null);
                try {
                  await login(values.email, values.password);
                  if (values.remember) localStorage.setItem("remember_email", values.email);
                  else localStorage.removeItem("remember_email");
                  navigate("/chat");
                } catch (err) {
                  setStatus(err.message || "Login failed. Please check your credentials and email verification status.");
                } finally {
                  setSubmitting(false);
                }
              }}
            >
              {({ isSubmitting, status, isValid, dirty }) => (
                <Form className="space-y-4">
                  {/* Email */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
                    <div className="relative">
                      <span className="absolute inset-y-0 left-3 flex items-center text-slate-500">
                        <FiMail />
                      </span>
                      <Field
                        type="email"
                        name="email"
                        placeholder="your.email@example.com"
                        className="block w-full rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100
                                   pl-10 pr-3 py-2.5 placeholder:text-slate-500
                                   focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-transparent"
                        autoComplete="email"
                      />
                    </div>
                    <ErrorMessage name="email" component="div" className="mt-1 text-xs text-rose-400" />
                  </div>

                  {/* Password */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
                    <div className="relative">
                      <span className="absolute inset-y-0 left-3 flex items-center text-slate-500">
                        <FiLock />
                      </span>
                      <Field
                        type={showPass ? "text" : "password"}
                        name="password"
                        placeholder="••••••••"
                        className="block w-full rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100
                                   pl-10 pr-12 py-2.5 placeholder:text-slate-500
                                   focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-transparent"
                        autoComplete="current-password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPass((v) => !v)}
                        className="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-200"
                        aria-label={showPass ? "Hide password" : "Show password"}
                      >
                        {showPass ? <FiEyeOff /> : <FiEye />}
                      </button>
                    </div>
                    <ErrorMessage name="password" component="div" className="mt-1 text-xs text-rose-400" />
                  </div>

                  {/* Status */}
                  {status ? (
                    <div className="text-sm text-rose-300 bg-rose-900/20 border border-rose-500/30 rounded-md px-3 py-2">
                      {status}
                    </div>
                  ) : null}

                  <div className="flex items-center justify-between">
                    <label className="inline-flex items-center gap-2 text-sm text-slate-300">
                      <Field
                        type="checkbox"
                        name="remember"
                        className="rounded border-white/20 bg-neutral-900/60 text-indigo-500 focus:ring-indigo-500/60"
                      />
                      Remember me
                    </label>
                    <Link to="/forgot" className="text-sm text-indigo-300 hover:text-indigo-200 hover:underline">
                      Forgot password?
                    </Link>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting || !(isValid && dirty)}
                    className="group relative w-full overflow-hidden rounded-xl py-2.5 font-semibold
                               text-white shadow-[0_8px_30px_rgba(99,102,241,0.35)]
                               bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)]
                               hover:shadow-[0_10px_40px_rgba(236,72,153,0.35)]
                               transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="relative z-10">{isSubmitting ? "Logging in..." : "Login"}</span>
                    <span className="absolute inset-0 translate-x-[-120%] group-hover:translate-x-0 transition-transform
                                     bg-white/10" />
                  </button>

                  <p className="text-center text-sm text-slate-400">
                    Don’t have an account?{" "}
                    <Link to="/register" className="text-indigo-300 hover:text-indigo-200 hover:underline">
                      Sign Up
                    </Link>
                  </p>
                </Form>
              )}
            </Formik>
          </div>
        </div>

        {/* small caption */}
        <p className="mt-6 text-center text-xs text-slate-500">
          AI‑assisted legal platform for clients, advocates, and research. 
        </p>
      </div>
    </div>
  );
}
