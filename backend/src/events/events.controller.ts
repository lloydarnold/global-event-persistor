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

import * as CATS from './../res/categories.json';

@Controller('events')
export class EventsController {
    constructor(private readonly eventsService: EventsService) {}

    @Post()
    /**
     * Create an event in the events database. If the associated region was not already registered
     * in the `regions` database, a record for it is also created.
     *
     * Post JSON fields:
     * @param timeStamp (required): string that can be converted to Date object (e.g. YYYY-MM-DD)
     * @param sentiment: number between -100 and 100
     * @param source (required): source of event, e.g. link to article or post where the event was found
     * @param category (required): category code of the event (see events.model.ts)
     * @param subcategory: string indicating subcategory of the event
     * @param detail: description of the event
     * @param actors: array of strings with names of actors involved in event
     * @param stocks: array of codes of stocks directly related to event
     *
     * @param continent: full name of continent of the event (e.g. "Europe")
     * @param country: full name of country of the event (e.g. "People's Republic of China")
     * @param state: administrative region within the country (can be state, province, etc.)
     * @param city: city of the event
     */
    async createEvent(@Res() response, @Body() eventCreationDTO: EventCreationDTO) {
        const newEvent = await this.eventsService.create(eventCreationDTO)
        return response.status(HttpStatus.CREATED).json({
            newEvent
        })
    }

    /**
     * Returns an array with every event in the `events` database
     */
    @Get('/get-all')
    async fetchAllEvents(@Res() response) {
        const events = await this.eventsService.findAllEvents()
        return response.status(HttpStatus.OK).json({
            events
        })
    }

    /**
     * Returns event in a given time range.
     *
     * Query structure:
     * @param from: beginning of time range, as a Date (or Datetime) string
     * @param to: end of time range (inclusive), as Date (or Datetime) string
     */
    @Get('/get-in-range')
    async fetchEventsInRange(@Res() response, @Query() query: QueryDTO) {
        console.log(`Queried events from ${query.from} to ${query.to}`)
        const events = await this.eventsService.findEventsInRange(query.from, query.to)
        return response.status(HttpStatus.OK).json({
            events
        })
    }

    /**
     * Returns every region in the `regions` database.
     */
    @Get('/get-regions')
    async fetchAllRegions(@Res() response) {
        const regions = await this.eventsService.findAllRegions()
        return response.status(HttpStatus.OK).json({
            regions
        })
    }

 /**
  *  Query by category
  *  @param category : String - category code
  *  @param subcategory : String - subcategory code. If left blank will return
  *    all all events in a category
  *
  *  PRE : subcategory in catCodes.category || subcategory = Null &&
  *     catCodes.category != Null
  */
  @Get('get-category')
  async fetchEventsByCategory(@Res() response, @Query() query: QueryDTO) {
    var cat = query.category;
    var sub :String| null = query.subcategory;

    if ( cat == null )
    {
      sub = null  // can't search subcategory if no category.
      console.log("Category query with no category")
    }
    else if ( sub == null )
    {
      console.log("Category query with no subcategory");
    }

    if ( sub == null || CATS[`${cat}`].includes(sub) ) {
      const events = await this.eventsService.findEventsOfCategory(cat, sub);
      return response.status(HttpStatus.OK).json({
          events
      })
    }

    console.log(`Queried events of type : ${cat}, subtype : ${sub}`);

  }

}
