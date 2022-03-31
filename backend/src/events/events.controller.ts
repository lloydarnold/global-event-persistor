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
  /** Create an event in the events database.
   * If the associated region was not already registered
   * in the `regions` database, a record for it is also created.
   *
   * Post JSON fields:
   * @param timeStamp (required): string that can be converted to Date object (e.g. YYYY-MM-DD)
   * @param  positivity: Number, number between -100 and 100
   * @param relevance : Number,
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

  /** Creates new event */
  async createEvent(@Res() response, @Body() eventCreationDTO: EventCreationDTO) {
    try {
      const newEvent = await this.eventsService.create(eventCreationDTO)
      return response.status(HttpStatus.CREATED).json({
        newEvent
      })
    } catch (e) {
        console.error(e)
        return response.status(HttpStatus.BAD_REQUEST).json({
            message: e.message
        })
    }
  }

  @Post('create-many')
  async createManyEvents(@Res() response, @Body() eventDTOArray: EventCreationDTO[]) {
    try {
      const newEvents = await this.eventsService.createMany(eventDTOArray)
      return response.status(HttpStatus.CREATED).json({
        newEvents
      })
    } catch (e) {
        console.error(e)
        return response.status(HttpStatus.BAD_REQUEST).json({
            message: e.message
        })
    }
  }

  /** Returns an array with every event in the `events` database
   */
  @Get('/get-all')
  async fetchAllEvents(@Res() response) {
      const events = await this.eventsService.findAllEvents()
      return response.status(HttpStatus.OK).json({
          events
      })
  }

 /** Returns event in a given time range
   *  Query structure:
   *  @param from: beginning of time range, as a Date (or Datetime) string
   *  @param to: end of time range (inclusive), as Date (or Datetime) string
   *
   * PRE : from, to are both in valid date format
   * TODO add validation on timestamp format
   */
  @Get('/get-in-range')
  async fetchEventsInRange(@Res() response, @Query() query: QueryDTO) {
      const myFrom = query.from;
      const myTo = query.to;

      console.log(`Queried events from ${myFrom} to ${myTo}`)
      try {
        const events = await this.eventsService.findEventsInRange(myFrom, myTo)
        return response.status(HttpStatus.OK).json({
            events
        })
    } catch (e) {
      // if error is due to failed casting of date, give a custom error message
        return response.status(HttpStatus.BAD_REQUEST).json({
            message: e.message
        })
      }
  }

  /** Returns every region in the `regions` database.
   */
  @Get('/get-regions')
  async fetchAllRegions(@Res() response) {
      const regions = await this.eventsService.findAllRegions()
      return response.status(HttpStatus.OK).json({
          regions
      })
  }


  /** Take a string, strip it of characters not in the Latin alphabet,
   *  convert to upper case
   *
   * @param toStrip : String string to be stripped and converted
   */
  private stripAccentsToUpper(toStrip: string) :string {
    require(toStrip) // if (toStrip == null) { return null }
    var r = toStrip.toLowerCase()
    r = r.replace(new RegExp(/\s/g),"");
    r = r.replace(new RegExp(/[àáâãäå]/g),"a");
    r = r.replace(new RegExp(/æ/g),"ae");
    r = r.replace(new RegExp(/ç/g),"c");
    r = r.replace(new RegExp(/[èéêë]/g),"e");
    r = r.replace(new RegExp(/[ìíîï]/g),"i");
    r = r.replace(new RegExp(/ñ/g),"n");
    r = r.replace(new RegExp(/[òóôõö]/g),"o");
    r = r.replace(new RegExp(/œ/g),"oe");
    r = r.replace(new RegExp(/[ùúûü]/g),"u");
    r = r.replace(new RegExp(/[ýÿ]/g),"y");
    r = r.replace(new RegExp(/\W/g),"");
    return r.toUpperCase()
  }

  /** Query events based on their region
.   *
   * API params :
   * @param continent : String
   * @param country : String
   * @param state : String
   * @param city : String
   *
   * PRE : continent, country, state are in ISO standard codes && city is full
    *      name, without accents
   */
  @Get('get-by-region')
  async fetchEventsInRegion(@Res() response, @Query() query: QueryDTO) {
      const city: string = query.city ? this.stripAccentsToUpper(query.city) : query.city
      var events =  await this.eventsService.findEventsInRegion(
                                          query.continent, query.country, query.state,
                                          city)

      return response.status(HttpStatus.OK).json({ events })

  }

/** Query by category
  *
  * API parameters :
  *  @param category : String - category code
  *  @param subcategory : String - subcategory code. If left blank will return
  *    all all events in a category
  *
  *  PRE : subcategory in catCodes.category || subcategory = Null &&
  *     catCodes.category != Null (ie, category exists) || category == null --
  *                                                         TODO review last condition
  */
  @Get('get-by-category')
  async fetchEventsByCategory(@Res() response, @Query() query: QueryDTO) {
    var cats = query.categories;
    var subs = query.subcategories;

    console.log(`Queried events of type : ${cats}, subtype : ${subs}`);
    try {
        const events = await this.eventsService.findEventsOfCategory(cats, subs);
        return response.status(HttpStatus.OK).json({
            events
        })
    } catch (e) {
        console.error(e)
        return response.status(HttpStatus.BAD_REQUEST).json({
            message: e.message
        })
    }
  }

 /** Query by stock / commodity
   *
   * API parameters :
   * @param stock : String - stock code, using code as traded on relevant market
   *
   * PRE : stock is one of the stocks we track
   *
   * TODO - add validation
   */
  @Get('/get-by-stock')
  async fetchByStock(@Res() response, @Query() query: QueryDTO) {
      const events = await this.eventsService.findByStock(query.stocks)
      return response.status(HttpStatus.OK).json({
          events
      })
  }

  /** general query
   *  A generalised query function; allows queries by any parameter that may
   *  otherwise by used.
   */
  @Get('get-events')
  async fetchEventsGeneral(@Res() response, @Query() query: QueryDTO) {
    try {
        const events = await this.eventsService.findEventsGeneral(query);
        return response.status(HttpStatus.OK).json({
            events
        })
    } catch (e) {
        console.error(e)
        return response.status(HttpStatus.BAD_REQUEST).json({
            message: e.message
        })
    }
  }

}
