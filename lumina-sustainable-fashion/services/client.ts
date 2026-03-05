const TOKEN_KEY = 'lumina_auth_token';

export const authToken = {
    get:()=> localStorage.getItem(TOKEN_KEY),
    set:(token:string)=> localStorage.setItem(TOKEN_KEY,token),
    clear : ()=> localStorage.removeItem(TOKEN_KEY),
};