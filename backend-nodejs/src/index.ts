import "dotenv/config";
import express from 'express';
import {authRouter} from './routes/auth';
import {ensureSchema,pool} from './lib/db';
import {errorHandler} from './middleware/errorHandler';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 4000;
app.use(express.json());
app.use(cors());


app.get('/health',(req,res)=>{
    res.status(200).json({status:'ok'});
})

app.use('/api/auth',authRouter);
app.use(errorHandler);

app.listen(PORT,async()=>{
    try{
        // Ensure database and schema exist first
        await ensureSchema();
        console.log('Database schema ensured');
        
        // Then test the connection
        await pool.getConnection().then(conn=>{
            console.log('Connected to MySQL database');
            conn.release();
        }).catch(err=>{
            console.error('Error connecting to MySQL database:',err);
        })
        
        console.log(`Server is running on port ${PORT}`);
    }catch(err){
        console.error('Error during server startup:',err);
        process.exit(1);
        

    }
})