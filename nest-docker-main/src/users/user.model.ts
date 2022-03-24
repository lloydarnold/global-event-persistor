import * as moongose from 'mongoose';

export const UserSchema = new moongose.Schema({
    name: {type: String, required: true},
    email: {type: String, required: true},
    password: {type: String, required: true},
});

export interface User extends moongose.Document {
    id: string;
    name: string;
    email: string;
    password: string;
}