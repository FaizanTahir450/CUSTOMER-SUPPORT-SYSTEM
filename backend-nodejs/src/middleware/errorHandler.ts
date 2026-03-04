import {Request,Response,NextFunction} from 'express';



export function errorHandler(req:Request,res:Response,Next:NextFunction){
const status = 500;
return res.status(status).json({
    error: {code: 'internal_server_error', message: 'An unexpected error occurred'}
});



}