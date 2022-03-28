import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Event, Region, EventCreationDTO } from './events.model';
import * as CATS from './../res/categories.json';

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

    /**
     * Create event
     * @param eventDict
     * TODO:
     *   done // - Verify region exists and create one if not
     *   - Parse relevant stocks
     */
    async create(eventCreationDTO: EventCreationDTO) : Promise<Event>{
        console.log(eventCreationDTO.detail)
        console.log(new this.eventModel(eventCreationDTO));
        console.log(new this.regionModel(eventCreationDTO));
        console.log(this.regionModel);
        console.log(eventCreationDTO.source)

        const docs = await this.regionModel.find( {
            continent: eventCreationDTO.continent,
            country: eventCreationDTO.country,
            state: eventCreationDTO.state,
            city:  eventCreationDTO.city
        }).exec()
        console.log(docs)
        var createdEvent = new this.eventModel(eventCreationDTO);
        var doc;
        if (docs.length == 0) {
            const createdRegion = new this.regionModel(eventCreationDTO)
            console.log(`Region ${createdRegion} did not exist but was created`);
            doc = createdRegion.save()
        }
        else doc = docs[0]
        eventCreationDTO.region = doc._id
        createdEvent = new this.eventModel(eventCreationDTO);
        return createdEvent.save();
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

    async findEventsInRegion(continent: String, country: String, state: String, city: String): Promise<Event[]> {
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
}
