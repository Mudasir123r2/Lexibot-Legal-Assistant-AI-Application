// src/pages/Register.jsx
import { useContext, useState } from "react";
import { AuthContext } from "../../context/AuthContext";
import { Link, useNavigate } from "react-router-dom";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { FaBalanceScale } from "react-icons/fa";
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff } from "react-icons/fi";

const RegisterSchema = Yup.object({
  name: Yup.string()
    .min(2, "Name must be at least 2 characters")
    .max(100, "Name is too long")
    .matches(/^[a-zA-Z\s]+$/, "Name can only contain letters and spaces")
    .required("Full name is required"),
  email: Yup.string()
    .email("Please enter a valid email address")
    .required("Email is required"),
  password: Yup.string()
    .min(8, "Password must be at least 8 characters")
    .max(72, "Password cannot exceed 72 characters")
    .required("Password is required"),
  role: Yup.mixed()
    .oneOf(["client", "advocate"], "Please select a valid role")
    .required("Please select your role"),
});

export default function Register() {
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();
  const [showPass, setShowPass] = useState(false);

  return (
    <div className="relative min-h-screen flex items-stretch overflow-hidden bg-[#0a0a0b]">
      {/* Dark mesh gradients (page background) */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(120%_90%_at_50%_0%,rgba(255,255,255,0.06)_0%,transparent_60%),radial-gradient(90%_70%_at_0%_0%,rgba(99,102,241,0.10)_0%,transparent_60%),radial-gradient(90%_70%_at_100%_0%,rgba(236,72,153,0.10)_0%,transparent_60%)]" />
        <div className="absolute -top-24 -left-24 h-80 w-80 rounded-full bg-gradient-to-tr from-indigo-500/20 via-fuchsia-500/10 to-emerald-400/10 blur-3xl" />
        <div className="absolute -bottom-24 -right-20 h-96 w-96 rounded-full bg-gradient-to-br from-fuchsia-600/15 to-indigo-600/10 blur-3xl" />
      </div>

      {/* Left hero (hidden on small screens) */}
      <section className="hidden lg:flex w-1/2 items-center justify-center p-12">
        <div className="max-w-md">
          <div className="mb-6">
            <div className="h-12 w-12 rounded-2xl bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10">
              <FaBalanceScale className="text-xl" />
            </div>
          </div>
          <h2 className="text-4xl font-extrabold leading-tight text-white">
            Empower Your Legal Journey with AI
          </h2>
          <p className="mt-4 text-slate-400">
            LexiBot transforms legal research, prediction, and assistance into clear, guided steps so complex judgments become usable insights. 
          </p>
        </div>
      </section>

      {/* Right form column */}
      <section className="flex w-full lg:w-1/2 items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
          {/* Halo border */}
          <div className="relative">
            <div className="absolute -inset-[2px] rounded-3xl bg-[conic-gradient(from_140deg,rgba(99,102,241,.35),rgba(236,72,153,.35),rgba(16,185,129,.35),rgba(99,102,241,.35))] blur md:blur-md opacity-70" />
            {/* Glass card */}
            <div className="relative rounded-3xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-[0_10px_40px_rgba(0,0,0,0.6)] p-8
                            bg-[radial-gradient(120%_120%_at_50%_-10%,rgba(255,255,255,0.07)_0%,transparent_55%)]">
              {/* Brand */}
              <div className="flex items-center justify-center gap-2 mb-2">
                <div className="h-10 w-10 rounded-xl bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10">
                  <FaBalanceScale className="text-lg" />
                </div>
                <span className="text-2xl font-semibold text-slate-100">LexiBot</span>
              </div>

              <h1 className="text-xl font-bold text-center text-white">Create Your Account</h1>
              <p className="text-center text-slate-400 text-sm mb-6">
                Join LexiBot to access AI‑powered legal assistance tailored for clients and advocates.
              </p>

              <Formik
                initialValues={{ name: "", email: "", password: "", role: "client" }}
                validationSchema={RegisterSchema}
                validateOnBlur
                validateOnChange
                onSubmit={async (values, { setStatus, setSubmitting, resetForm }) => {
                  setStatus(null);
                  try {
                    const data = await register(values);
                    resetForm();
                    setStatus(data.message || "Registration successful! Please check your email to verify your account.");
                    setTimeout(() => {
                      navigate("/login", { replace: true });
                    }, 3000);
                  } catch (err) {
                    setStatus(err.message || "Registration failed. Please try again.");
                  } finally {
                    setSubmitting(false);
                  }
                }}
              >
                {({ isSubmitting, status, isValid, dirty, values, setFieldValue }) => (
                  <Form className="space-y-4">
                    {/* Full Name */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
                      <div className="relative">
                        <span className="absolute inset-y-0 left-3 flex items-center text-slate-500">
                          <FiUser />
                        </span>
                        <Field
                          type="text"
                          name="name"
                          placeholder="Your Full Name"
                          className="block w-full rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100
                                     pl-10 pr-3 py-2.5 placeholder:text-slate-500
                                     focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-transparent"
                          autoComplete="name"
                        />
                      </div>
                      <ErrorMessage name="name" component="div" className="mt-1 text-xs text-rose-400" />
                    </div>

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
                          placeholder="your@example.com"
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
                          placeholder="Enter your password"
                          className="block w-full rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100
                                     pl-10 pr-12 py-2.5 placeholder:text-slate-500
                                     focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-transparent"
                          autoComplete="new-password"
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

                    {/* Role selection (Client / Advocate) */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Your Role</label>
                      <div className="flex items-center gap-6">
                        <label className="inline-flex items-center gap-2 text-sm text-slate-300">
                          <input
                            type="radio"
                            name="role"
                            value="client"
                            checked={values.role === "client"}
                            onChange={() => setFieldValue("role", "client")}
                            className="text-indigo-500 bg-neutral-900/60 border-white/20 focus:ring-indigo-500/60"
                          />
                          Client
                        </label>
                        <label className="inline-flex items-center gap-2 text-sm text-slate-300">
                          <input
                            type="radio"
                            name="role"
                            value="advocate"
                            checked={values.role === "advocate"}
                            onChange={() => setFieldValue("role", "advocate")}
                            className="text-indigo-500 bg-neutral-900/60 border-white/20 focus:ring-indigo-500/60"
                          />
                          Advocate
                        </label>
                      </div>
                      <ErrorMessage name="role" component="div" className="mt-1 text-xs text-rose-400" />
                    </div>

                    {/* Status */}
                    {status ? (
                      <div className={`text-sm rounded-md px-3 py-2 ${
                        (status.toLowerCase().includes("successful") || status.toLowerCase().includes("check your email")) && !status.toLowerCase().includes("already exists")
                          ? "text-indigo-200 bg-indigo-900/20 border border-indigo-500/30"
                          : "text-rose-300 bg-rose-900/20 border border-rose-500/30"
                      }`}>
                        {status}
                      </div>
                    ) : null}

                    {/* Actions */}
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => navigate("/login")}
                        className="flex-1 rounded-xl border border-white/15 bg-neutral-900/40 text-slate-200 py-2.5
                                   hover:bg-neutral-800/60 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={isSubmitting || !(isValid && dirty)}
                        className="flex-1 group relative overflow-hidden rounded-xl py-2.5 font-semibold text-white
                                   shadow-[0_8px_30px_rgba(99,102,241,0.35)]
                                   bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)]
                                   hover:shadow-[0_10px_40px_rgba(236,72,153,0.35)]
                                   transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <span className="relative z-10">{isSubmitting ? "Registering..." : "Register"}</span>
                        <span className="absolute inset-0 translate-x-[-120%] group-hover:translate-x-0 transition-transform bg-white/10" />
                      </button>
                    </div>

                    <p className="text-center text-sm text-slate-400">
                      Already have an account?{" "}
                      <Link to="/login" className="text-indigo-300 hover:text-indigo-200 hover:underline">
                        Log In
                      </Link>
                    </p>
                  </Form>
                )}
              </Formik>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
