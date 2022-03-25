import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { EventSchema, RegionSchema } from './events.model' 
import { EventsService } from './events.service'
import { EventsController } from './events.controller';

@Module({
    imports: [
        MongooseModule.forFeature([
            { name: 'Event', schema: EventSchema }
        ], 'events'),
        MongooseModule.forFeature([
            { name: 'Region', schema: RegionSchema }
        ], 'regions'),
    ],
    controllers: [EventsController],
    providers: [EventsService],
})
export class EventsModule {}
