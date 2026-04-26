import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-reclutamiento',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './reclutamiento.html',
  styleUrl: './reclutamiento.css'
})
export class Reclutamiento {
  rqs: any[] = [];

  constructor(private rqService: RqService) {
    this.rqs = this.rqService.getAll();
  }
}
