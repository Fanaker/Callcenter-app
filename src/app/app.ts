import { Component, signal } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Navbar } from "./shared/navbar/navbar";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, Navbar],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('callcenter-app');

  constructor(private router: Router) {}

isLoginPage(): boolean {
  return this.router.url === '/' || this.router.url.includes('login');
  }
}
