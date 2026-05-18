export interface Postulante {
  id: number;
  rqId: string;
  dni: string;
  nombre: string;
  apellido: string;
  correo: string;
  telefono: string;
  medioPreferido: 'WHATSAPP' | 'LLAMADA' | 'CORREO';
  cvUrl: string;
  fechaRegistro: string;

  apto: boolean;
  entrevistaAprobada: boolean;
  seleccionado: boolean;
  contratado: boolean;
}