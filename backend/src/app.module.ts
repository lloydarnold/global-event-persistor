import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ConfigModule } from '@nestjs/config'

const envModule = ConfigModule.forRoot()

import { AppController } from './app.controller';
import { AppService } from './app.service';
import { EventsController } from './events/events.controller';
import { EventsService } from './events/events.service';
import { EventsModule } from './events/events.module';

console.log(`mongodb+srv:${process.env.MONGO_ATLAS_USER}:${process.env.MONGO_ATLAS_PASSWORD}@cluster0.${process.env.MONGO_ATLAS_CODE}.mongodb.net/events?retryWrites=true&w=majority`,)
@Module({
  imports: [
    envModule,
    EventsModule,
    MongooseModule.forRoot(
      `mongodb+srv://${process.env.MONGO_ATLAS_USER}:${process.env.MONGO_ATLAS_PASSWORD}@cluster0.${process.env.MONGO_ATLAS_CODE}.mongodb.net/events?retryWrites=true&w=majority`,
      { connectionName: 'events' }      
    ),
    MongooseModule.forRoot(
      `mongodb+srv://${process.env.MONGO_ATLAS_USER}:${process.env.MONGO_ATLAS_PASSWORD}@cluster0.${process.env.MONGO_ATLAS_CODE}.mongodb.net/regions?retryWrites=true&w=majority`,
      { connectionName: 'regions' }   
    )
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
