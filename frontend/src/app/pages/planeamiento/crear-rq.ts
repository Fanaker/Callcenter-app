import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { RqService } from '../../services/rq';
import { Campania } from '../../models/campania.model';
import { Puesto } from '../../models/puesto.model';
import { Rq } from '../../models/rq.model';

@Component({
  selector: 'app-crear-rq',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './crear-rq.html',
  styleUrl: './crear-rq.css'
})
export class CrearRq implements OnInit {
  cantidad = 0;
  fechaIngreso = '';
  fechaFinCapacitacion = '';
  fechaInicioCapacitacion = '';
  diasCapacitacion = 0;
  comentarios = '';

  campaniasActivas: Campania[] = [];
  puestosActivos: Puesto[] = [];

  campaniaId: number | null = null;
  puestoId: number | null = null;

  errorFechaFinCapacitacion = '';
  errorFechaInicioCapacitacion = '';

  constructor(
    private rqService: RqService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.campaniasActivas = this.rqService.getCampaniasActivas();
    this.puestosActivos = this.rqService.getPuestosActivos();
  }

  isFormValid(): boolean {
    return (
      this.campaniaId !== null &&
      this.puestoId !== null &&
      this.cantidad > 0 &&
      this.diasCapacitacion > 0 &&
      this.fechaIngreso !== '' &&
      this.fechaInicioCapacitacion !== '' &&
      this.fechaFinCapacitacion !== '' &&
      this.errorFechaInicioCapacitacion === '' &&
      this.errorFechaFinCapacitacion === ''
    );
  }

  getSelectedCampaniaName(): string {
    const campania = this.campaniasActivas.find(
      (item) => item.id === Number(this.campaniaId)
    );

    return campania?.nombre || 'Sin campaña seleccionada';
  }

  getSelectedPuestoName(): string {
    const puesto = this.puestosActivos.find(
      (item) => item.id === Number(this.puestoId)
    );

    return puesto?.nombre || 'Sin puesto seleccionado';
  }

  goBack(): void {
    this.router.navigate(['/planeamiento']);
  }

  crearRQ(): void {
    this.errorFechaFinCapacitacion = '';
    this.errorFechaInicioCapacitacion = '';

    if (this.campaniaId === null) {
      alert('❌ Debes seleccionar una campaña');
      return;
    }

    if (this.puestoId === null) {
      alert('❌ Debes seleccionar un puesto');
      return;
    }

    if (!this.validarRQ()) {
      return;
    }

    const campaniaIdSeleccionada = Number(this.campaniaId);
    const puestoIdSeleccionado = Number(this.puestoId);

    const campaniaSeleccionada = this.campaniasActivas.find(
      (campania) => campania.id === campaniaIdSeleccionada
    );

    const puestoSeleccionado = this.puestosActivos.find(
      (puesto) => puesto.id === puestoIdSeleccionado
    );

    if (!campaniaSeleccionada || !puestoSeleccionado) {
      alert('❌ Error: campaña o puesto no encontrado');
      return;
    }

    const rq: Partial<Rq> = {
      codigo: this.rqService.generateCode(),
      campaniaId: campaniaIdSeleccionada,
      campaign: campaniaSeleccionada.nombre,
      puestoId: puestoIdSeleccionado,
      puesto: puestoSeleccionado.nombre,
      comentarios: this.comentarios.trim(),
      cantidad: this.cantidad,
      diasCapacitacion: this.diasCapacitacion,
      fechaIngreso: this.fechaIngreso,
      fechaInicioCapacitacion: this.fechaInicioCapacitacion,
      fechaFinCapacitacion: this.fechaFinCapacitacion,
      estado: 'ABIERTO'
    };

    this.rqService.add(rq);
    this.router.navigate(['/planeamiento']);
  }

  validarRQ(): boolean {
    let isValid = true;

    if (
      this.cantidad <= 0 ||
      this.fechaIngreso === '' ||
      this.fechaFinCapacitacion === '' ||
      this.fechaInicioCapacitacion === '' ||
      this.diasCapacitacion <= 0
    ) {
      alert('❌ Completa todos los campos correctamente');
      return false;
    }

    const fechaIngreso = new Date(this.fechaIngreso);
    const fechaFin = new Date(this.fechaFinCapacitacion);
    const fechaInicioCap = new Date(this.fechaInicioCapacitacion);
    const diaMs = 24 * 60 * 60 * 1000;

    if (fechaFin >= fechaIngreso) {
      this.errorFechaFinCapacitacion =
        'La fecha de fin de capacitación debe ser anterior a la fecha prevista de inicio del personal.';
      isValid = false;
    } else {
      this.errorFechaFinCapacitacion = '';
    }

    if (fechaFin.getTime() - fechaInicioCap.getTime() < 3 * diaMs) {
      this.errorFechaInicioCapacitacion =
        'La fecha de inicio de capacitación debe ser al menos 3 días anterior a la fecha de fin de capacitación.';
      isValid = false;
    } else {
      this.errorFechaInicioCapacitacion = '';
    }

    return isValid;
  }

  onFechaChange(): void {
    if (this.fechaIngreso && this.fechaFinCapacitacion) {
      const fechaIngreso = new Date(this.fechaIngreso);
      const fechaFin = new Date(this.fechaFinCapacitacion);

      if (fechaFin >= fechaIngreso) {
        this.errorFechaFinCapacitacion =
          'La fecha de fin de capacitación debe ser anterior a la fecha prevista de inicio del personal.';
      } else {
        this.errorFechaFinCapacitacion = '';
      }
    }

    if (this.fechaInicioCapacitacion && this.fechaFinCapacitacion) {
      const fechaInicioCap = new Date(this.fechaInicioCapacitacion);
      const fechaFin = new Date(this.fechaFinCapacitacion);
      const diaMs = 24 * 60 * 60 * 1000;

      if (fechaFin.getTime() - fechaInicioCap.getTime() < 3 * diaMs) {
        this.errorFechaInicioCapacitacion =
          'La fecha de inicio de capacitación debe ser al menos 3 días anterior a la fecha de fin de capacitación.';
      } else {
        this.errorFechaInicioCapacitacion = '';
      }
    }
  }
}