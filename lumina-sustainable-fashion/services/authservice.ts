

export async function signup(payload: { email: string; password: string; name?: string }) {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    let data;
    try {
        data = await res.json();
    } catch (e) {
        throw new Error(`Server error: ${res.statusText}`);
    }
    
    if (!res.ok) {
        throw new Error(data.error?.message || 'Signup Failed');
    }
    return data as { user: { id: string; email: string; name?: string; created_at: string }; token: string }
}

export async function login(payload:{email:string;password:string}){
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/login`,{
        method : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    let data;
    try {
        data = await res.json();
    } catch (e) {
        throw new Error(`Server error: ${res.statusText}`);
    }
    if(!res.ok){
        throw new  Error(data?.error?.message || 'Login Failed');
    }
    return data as {user:{id:string;email:string;name?:string;created_at:string};token:string};
}

export async function forgetPassword(payload: { email: string }) {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/forget-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    let data;
    try {
        data = await res.json();
    } catch (e) {
        throw new Error(`Server error: ${res.statusText}`);
    }
    
    if (!res.ok) {
        throw new Error(data?.error?.message || 'Failed to send reset email');
    }
    
    return data as { message: string };
}

export async function resetPassword(payload: { token: string; newPassword: string }) {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    let data;
    try {
        data = await res.json();
    } catch (e) {
        throw new Error(`Server error: ${res.statusText}`);
    }
    
    if (!res.ok) {
        throw new Error(data?.error?.message || 'Failed to reset password');
    }
    
    return data as { message: string };
}