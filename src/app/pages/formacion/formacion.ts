import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-formacion',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './formacion.html',
  styleUrl: './formacion.css'
})
export class Formacion {
  rqs: any[] = [];

  constructor(private rqService: RqService) {
    this.rqs = this.rqService.getAll();
  }
}
