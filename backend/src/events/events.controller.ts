import { 
    Controller,
    Body,
    Post,
    Get,
    HttpStatus,
    Param,
    Res,
    Query
} from '@nestjs/common';
import { response } from 'express';
import { EventCreationDTO, QueryDTO } from './events.model'
import { EventsService } from './events.service'

@Controller('events')
export class EventsController {
    constructor(private readonly eventsService: EventsService) {}

    @Post()
    async createEvent(@Res() response, @Body() eventCreationDTO: EventCreationDTO) {
        const newEvent = await this.eventsService.create(eventCreationDTO)
        return response.status(HttpStatus.CREATED).json({
            newEvent
        })
    }

    @Get('/get-all')
    async fetchAllEvents(@Res() response) {
        const events = await this.eventsService.findAllEvents()
        return response.status(HttpStatus.OK).json({
            events
        })
    }

    @Get('/get-in-range')
    async fetchEventsInRange(@Res() response, @Query() query: QueryDTO) {
        console.log(`Queried events from ${query.from} to ${query.to}`)
        const events = await this.eventsService.findEventsInRange(query.from, query.to)
        return response.status(HttpStatus.OK).json({
            events
        })
    }

    @Get('/get-regions')
    async fetchAllRegions(@Res() response) {
        const regions = await this.eventsService.findAllRegions()
        return response.status(HttpStatus.OK).json({
            regions
        })
    }

}
