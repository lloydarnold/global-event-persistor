import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UsersController } from './users/users.controller';
import { UsersService } from './users/users.service';
import { UsersModule } from './users/users.module';
import { MongooseModule } from '@nestjs/mongoose';

@Module({
  imports: [
    UsersModule,
    MongooseModule.forRoot(
      `mongodb+srv://${process.env.MONGO_ATLAS_USER}:${process.env.MONGO_ATLAS_PASSWORD}@cluster0.eo7am.mongodb.net/${process.env.MONGO_ATLAS_DB}?retryWrites=true&w=majority`,),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
