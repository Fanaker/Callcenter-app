export type MedioPreferido = 'whatsapp' | 'llamada' | 'email';

export interface Postulante {
  id: number;
  rqCodigo: string;

  nombre: string;
  apellido: string;
  dni: string;
  correo: string;
  telefono: string;
  medioPreferido: MedioPreferido;

  cvUrl: string;
  comentarios: string;

  apto: boolean;
  entrevistaAprobada: boolean;
  elegido: boolean;
  contratar: boolean;

  test1: number;
  test2: number;
  test3: number;
  test4: number;
  test5: number;
}