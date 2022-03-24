import {
  Controller,
  Post,
  Body,
  Get,
  Param,
  Patch,
  Delete,
  Res,
  HttpStatus,
  Put
} from '@nestjs/common';
import { UsersService } from './users.service';
import { User } from './user.model';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  async create(@Body('name') name: string, @Body('email') email: string, @Body('password') password: string) {
    const generatedId = await this.usersService.create(name, email, password);
    return { id: generatedId };
  }

  @Get()
  async findAll(): Promise<any> {
    return this.usersService.findAll();
  }

  @Get(':id')
  async findById(@Res() response, @Param('id') id) {
      const user = await this.usersService.readById(id);
      return response.status(HttpStatus.OK).json({
          user
      })
  }

  @Delete('delete/:id')
  async Delete(@Param('id') id){
    await this.usersService.delete(id);
  }

  @Put('update/:id')
    async update(@Res() response, @Param('id') id, @Body() user: User) {
        const updatedUser = await this.usersService.update(id, user);
        return response.status(HttpStatus.OK).json({
            updatedUser
        })
    }

}
