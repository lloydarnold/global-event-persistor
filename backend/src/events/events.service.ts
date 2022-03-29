import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Event, Region, EventCreationDTO, QueryDTO } from './events.model';
import * as CATS from './../res/categories.json';
import * as CONTS from './../res/continents.json'

@Injectable()
export class EventsService {
    constructor (
        @InjectModel('Event') private readonly eventModel: Model<Event>,
        @InjectModel('Region') private readonly regionModel: Model<Region>){

        }

    // separateEventRegion(eventCreationDTO: EventCreationDTO) {
    //     const event : Event = {
    //         id: eventCreationDTO.id,
    //         timeStamp: eventCreationDTO.timeStamp,
    //         sentiment: eventCreationDTO.sentiment,
    //         source: eventCreationDTO.source,
    //         category: eventCreationDTO.category,
    //         subcategory: eventCreationDTO.subcategory,
    //         detail: eventCreationDTO.detail,
    //         region: eventCreationDTO.region,
    //         actors: eventCreationDTO.actors,
    //         stocks: eventCreationDTO.stocks,
    //     }
    //     const region : Region = {
    //         id_reg: eventCreationDTO.id_reg,
    //         continent : eventCreationDTO.continent,
    //         country : eventCreationDTO.country,
    //         state: eventCreationDTO.state, // state, province, county, etc; varies
    //         city : eventCreationDTO.city,
    //     }
    // }

    /** Create event
      *  @param eventDict
      *   Verifies if region exists and create one if not
      *   TODO (?) - Parse relevant stocks - is this the place or is that a job
      *     for scrapers ?
      *
      * PRE : continent, country, state are in correct form
      */
    async create(eventCreationDTO: EventCreationDTO) : Promise<Event>{
        console.log(eventCreationDTO.detail);
        console.log(new this.eventModel(eventCreationDTO));
        console.log(new this.regionModel(eventCreationDTO));
        console.log(this.regionModel);
        console.log(eventCreationDTO.source);

        var myRegion = {
          continent: eventCreationDTO.continent,
          country: eventCreationDTO.country,
          state: eventCreationDTO.state,
          city:  eventCreationDTO.city
        };

        this.validateRegion(myRegion)

        const docs = await this.regionModel.find( {
          myRegion
        }).exec();
        console.log(docs);
        var createdEvent = new this.eventModel(eventCreationDTO);
        var doc;
        if (docs.length == 0) {
            const createdRegion = new this.regionModel(eventCreationDTO)
            console.log(`Region ${createdRegion} did not exist but was created`);
            doc = await createdRegion.save()
        }
        else doc = docs[0]
        eventCreationDTO.region = doc._id
        console.log(doc)
        console.log(eventCreationDTO)
        createdEvent = new this.eventModel(eventCreationDTO);
        return createdEvent.save();
    }

    private validateRegion( toCheck ) {
        console.log(toCheck)
      }

    async findAllEvents(): Promise<Event[]> {
        return this.eventModel.find().exec();
    }

    async findAllRegions(): Promise<Region[]> {
        return this.regionModel.find().exec();
    }

    async findEventsInRange(from: Date, to: Date): Promise<Event[]> {
        return this.eventModel.find({
            timeStamp: { $gte: from, $lte: to }
        }).exec();
    }

    async findEventsInRegion(continent: String, country: String, state: String, city: String|null): Promise<Event[]> {
        var regionAttributes = {
            continent: continent,
            country: country,
            state: state,
            city: city,
        }

        console.log(regionAttributes)

        // delete unspecified fields, thus defaulting to `ALL`
        Object.keys(regionAttributes).forEach(key => {
            if (regionAttributes[key] == undefined) {
                delete regionAttributes[key]
            }
        })

        const regions = await this.regionModel.find(regionAttributes).exec()

        return this.eventModel.find({
            'region': { $in: regions }
        }).exec()
    }

    async findEventsOfCategory(cat: String, sub: String ): Promise<Event[]> {
      if ( cat == null ) {
        console.log("Category query with no category");
        // TODO review if this makes sense or if we should throw an error.
        return this.eventModel.find({}).exec();
      }

      else if ( sub == null ) {
        console.log("Category query with no subcategory");
        return this.eventModel.find({ category: cat }).exec();
      }

      if (!(CATS[`${cat}`].includes(sub)))
        throw new Error("Subcategory does not belong to the given category")

      return this.eventModel.find({
        category: cat,
        subcategory : sub,
      });
    }

    async findByStock(stock: String) {
      return this.eventModel.find({ stocks: stock }).exec()
    }

    private timeMillis(date: Date) : number {
      return new Date(date).getTime()
    }

    async findEventsGeneral(query: QueryDTO) {
      var eventsQuery = this.eventModel.find();

      if (query.stock) eventsQuery.where('stocks').equals(query.stock)

      if (query.from) eventsQuery.where('timeStamp').gte(this.timeMillis(query.from))
      if (query.to) eventsQuery.where('timeStamp').lte(this.timeMillis(query.to))

      if (query.category) {
        eventsQuery.where('category').equals(query.category)
        if (query.subcategory) {
          if (!(CATS[`${query.category}`].includes(query.subcategory)))
            throw new Error("Subcategory does not belong to the given category")
            eventsQuery.where('subcategory').equals(query.subcategory)
        }
      }

      var regionAttributes = {
        continent: query.continent,
        country: query.country,
        state: query.state,
        city: query.city,
      }
      console.log(regionAttributes)

      // delete unspecified fields, thus defaulting to `ALL`
      Object.keys(regionAttributes).forEach(key => {
          if (regionAttributes[key] == undefined) {
              delete regionAttributes[key]
          }
      })

      if (Object.keys(regionAttributes).length > 0) {
        const regions = await this.regionModel.find(regionAttributes).exec()
        eventsQuery.where('region').in(regions);
      }

      return eventsQuery.exec()
    }
}
