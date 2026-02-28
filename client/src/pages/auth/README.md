# Authentication Forms - Validation Guide

## Frontend Validation (Yup Schema)

### Register Form
- **Name**: 2-100 characters, letters and spaces only
- **Email**: Valid email format
- **Password**: 6-72 characters (72 is bcrypt's maximum)
- **Role**: Must be "client" or "advocate"

### Login Form
- **Email**: Valid email format
- **Password**: 6-72 characters

## Backend Validation (Pydantic)

### UserCreate Model
- **Name**: Trimmed, 2-100 characters
- **Email**: Valid EmailStr format
- **Password**: 6-72 characters (enforced for bcrypt compatibility)
- **Role**: Enum of client/advocate/admin

## Common Error Messages

### Registration Errors
- ✅ "This email is already registered. Please use a different email or try logging in."
- ✅ "Password must be at least 6 characters long"
- ✅ "Password cannot exceed 72 characters (bcrypt limit)"
- ✅ "Name must be at least 2 characters long"

### Login Errors
- ✅ "Invalid credentials" (wrong email/password)
- ✅ "Please verify your email before signing in"
- ✅ "Your account has been deactivated"

## To Delete Existing User from Database

If you need to delete the existing user to test registration:

```javascript
// In MongoDB Compass or mongosh:
db.users.deleteOne({ email: "mudasirmujtabakhas@gmail.com" })
```

Or use the admin API endpoint once logged in as admin.
